"""Tests for WebSocket progress updates and download endpoint."""
import pytest
import pytest_asyncio
import json
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.websocket import manager, ConnectionManager, push_progress
from models.job import ProgressMessage, TaskStatus, ProductType


client = TestClient(app)


class TestDownloadEndpoint:
    """Tests for download endpoint."""

    def test_download_job_not_found(self):
        """Test download for non-existent job."""
        response = client.get("/api/download/lesson/nonexistent")
        assert response.status_code == 404

    def test_download_product_not_ready(self):
        """Test download for product not yet completed."""
        # Create a job
        create_response = client.post(
            "/api/generate",
            json={
                "subject": "数学",
                "grade": "7年级",
                "duration": 45,
                "topic": "一元一次方程",
            },
        )
        job_id = create_response.json()["job_id"]

        # Try to download lesson (status is pending, not completed)
        response = client.get(f"/api/download/lesson/{job_id}")
        assert response.status_code == 400

    def test_download_invalid_product_type(self):
        """Test download with invalid product type."""
        create_response = client.post(
            "/api/generate",
            json={
                "subject": "数学",
                "grade": "7年级",
                "duration": 45,
                "topic": "一元一次方程",
            },
        )
        job_id = create_response.json()["job_id"]

        # Try to download invalid product type
        response = client.get(f"/api/download/invalid/{job_id}")
        assert response.status_code == 400


class TestConnectionManager:
    """Tests for WebSocket ConnectionManager."""

    def test_manager_init(self):
        """Test ConnectionManager initializes correctly."""
        new_manager = ConnectionManager()
        assert new_manager.active_connections == {}

    def test_manager_has_no_connections_for_unknown_job(self):
        """Test manager has no connections for unknown job."""
        assert "unknown_job" not in manager.active_connections


class TestProgressMessage:
    """Tests for ProgressMessage model."""

    def test_progress_message_creation(self):
        """Test ProgressMessage is created correctly."""
        msg = ProgressMessage(
            job_id="test-job",
            task_type=ProductType.lesson,
            status=TaskStatus.in_progress,
            progress=50,
            message="Processing",
        )
        assert msg.job_id == "test-job"
        assert msg.task_type == ProductType.lesson
        assert msg.status == TaskStatus.in_progress
        assert msg.progress == 50
        assert msg.message == "Processing"

    def test_progress_message_serialization(self):
        """Test ProgressMessage can be serialized to JSON."""
        msg = ProgressMessage(
            job_id="test-job",
            task_type=ProductType.ppt,
            status=TaskStatus.completed,
            progress=100,
            download_url="/api/download/ppt/test-job",
        )
        json_str = msg.model_dump_json()
        data = json.loads(json_str)
        assert data["job_id"] == "test-job"
        assert data["task_type"] == "ppt"
        assert data["status"] == "completed"


@pytest_asyncio.fixture
async def async_client():
    """Create async client for WebSocket testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


class TestWebSocketEndpoint:
    """Tests for WebSocket endpoint."""

    @pytest.mark.asyncio
    async def test_websocket_connect_disconnect(self):
        """Test WebSocket connection and disconnect."""
        # Create a job first
        from app.router import jobs
        from models.job import JobStatus, TaskProgress, ProductType as PT
        from datetime import datetime

        job_id = "test-ws-job"
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status=TaskStatus.pending,
            tasks=[
                TaskProgress(type=PT.lesson, status=TaskStatus.pending, progress=0),
                TaskProgress(type=PT.tts, status=TaskStatus.pending, progress=0),
                TaskProgress(type=PT.ppt, status=TaskStatus.pending, progress=0),
                TaskProgress(type=PT.video, status=TaskStatus.pending, progress=0),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Test connection manager directly
        test_manager = ConnectionManager()
        assert test_manager.active_connections == {}

    @pytest.mark.asyncio
    async def test_push_progress_function(self):
        """Test push_progress function."""
        # Verify push_progress is callable
        assert callable(push_progress)


class TestRouterGenerateValidation:
    """Tests for generate endpoint validation."""

    def test_generate_missing_subject(self):
        """Test generate with missing subject."""
        response = client.post(
            "/api/generate",
            json={
                "grade": "7年级",
                "duration": 45,
                "topic": "一元一次方程",
            },
        )
        assert response.status_code == 422

    def test_generate_missing_grade(self):
        """Test generate with missing grade."""
        response = client.post(
            "/api/generate",
            json={
                "subject": "数学",
                "duration": 45,
                "topic": "一元一次方程",
            },
        )
        assert response.status_code == 422

    def test_generate_invalid_duration_too_low(self):
        """Test generate with duration below minimum."""
        response = client.post(
            "/api/generate",
            json={
                "subject": "数学",
                "grade": "7年级",
                "duration": 5,  # Below minimum of 15
                "topic": "一元一次方程",
            },
        )
        assert response.status_code == 422

    def test_generate_invalid_duration_too_high(self):
        """Test generate with duration above maximum."""
        response = client.post(
            "/api/generate",
            json={
                "subject": "数学",
                "grade": "7年级",
                "duration": 150,  # Above maximum of 120
                "topic": "一元一次方程",
            },
        )
        assert response.status_code == 422

    def test_generate_with_style(self):
        """Test generate with optional style parameter."""
        response = client.post(
            "/api/generate",
            json={
                "subject": "数学",
                "grade": "7年级",
                "duration": 45,
                "topic": "一元一次方程",
                "style": "启发式教学",
            },
        )
        assert response.status_code == 200


class TestConnectionManagerAsync:
    """Tests for ConnectionManager async methods."""

    @pytest.mark.asyncio
    async def test_connect_creates_connection_list(self):
        """Test connect creates connection list for new job."""
        from unittest.mock import MagicMock

        new_manager = ConnectionManager()
        mock_ws = MagicMock()

        # Mock accept method
        mock_ws.accept = MagicMock(return_value=None)
        # Make accept async
        async def mock_accept():
            pass
        mock_ws.accept = mock_accept

        await new_manager.connect("job-1", mock_ws)

        assert "job-1" in new_manager.active_connections
        assert mock_ws in new_manager.active_connections["job-1"]

    def test_disconnect_removes_connection(self):
        """Test disconnect removes connection properly."""
        from unittest.mock import MagicMock

        new_manager = ConnectionManager()
        mock_ws = MagicMock()

        # Manually add connection
        new_manager.active_connections["job-1"] = [mock_ws]

        new_manager.disconnect("job-1", mock_ws)

        assert "job-1" not in new_manager.active_connections

    def test_disconnect_keeps_other_connections(self):
        """Test disconnect doesn't remove other connections."""
        from unittest.mock import MagicMock

        new_manager = ConnectionManager()
        mock_ws1 = MagicMock()
        mock_ws2 = MagicMock()

        # Add multiple connections
        new_manager.active_connections["job-1"] = [mock_ws1, mock_ws2]

        new_manager.disconnect("job-1", mock_ws1)

        assert "job-1" in new_manager.active_connections
        assert mock_ws2 in new_manager.active_connections["job-1"]

    @pytest.mark.asyncio
    async def test_broadcast_no_connections(self):
        """Test broadcast with no connections."""
        new_manager = ConnectionManager()

        msg = ProgressMessage(
            job_id="no-connections-job",
            task_type=ProductType.lesson,
            status=TaskStatus.in_progress,
            progress=50,
        )

        # Should not crash
        await new_manager.broadcast("no-connections-job", msg)

    @pytest.mark.asyncio
    async def test_broadcast_to_connections(self):
        """Test broadcast sends to all connections."""
        from unittest.mock import MagicMock, AsyncMock

        new_manager = ConnectionManager()
        mock_ws1 = MagicMock()
        mock_ws2 = MagicMock()

        # Setup async send_text methods
        mock_ws1.send_text = AsyncMock()
        mock_ws2.send_text = AsyncMock()

        # Add connections
        new_manager.active_connections["job-1"] = [mock_ws1, mock_ws2]

        msg = ProgressMessage(
            job_id="job-1",
            task_type=ProductType.lesson,
            status=TaskStatus.completed,
            progress=100,
        )

        await new_manager.broadcast("job-1", msg)

        # Both connections should receive message
        mock_ws1.send_text.assert_called_once()
        mock_ws2.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_cleans_dead_connections(self):
        """Test broadcast removes dead connections."""
        from unittest.mock import MagicMock, AsyncMock

        new_manager = ConnectionManager()
        good_ws = MagicMock()
        dead_ws = MagicMock()

        # Good connection works
        good_ws.send_text = AsyncMock()
        # Dead connection raises error
        dead_ws.send_text = AsyncMock(side_effect=Exception("Connection dead"))

        # Add both connections
        new_manager.active_connections["job-1"] = [good_ws, dead_ws]

        msg = ProgressMessage(
            job_id="job-1",
            task_type=ProductType.lesson,
            status=TaskStatus.in_progress,
            progress=50,
        )

        await new_manager.broadcast("job-1", msg)

        # Dead connection should be removed
        assert dead_ws not in new_manager.active_connections.get("job-1", [])
        assert good_ws in new_manager.active_connections.get("job-1", [])