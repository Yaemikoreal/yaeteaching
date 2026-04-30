"""Tests for WebSocket connection management."""
import pytest
import pytest_asyncio
import json
from unittest.mock import MagicMock, AsyncMock
from app.websocket import ConnectionManager, manager, push_progress
from models.job import ProgressMessage, TaskStatus, ProductType


class TestConnectionManager:
    """Tests for ConnectionManager class."""

    def test_connection_manager_init(self):
        """Test ConnectionManager initializes with empty connections."""
        cm = ConnectionManager()
        assert cm.active_connections == {}

    @pytest.mark.asyncio
    async def test_connection_manager_connect(self):
        """Test connect adds websocket to active connections."""
        cm = ConnectionManager()
        mock_ws = AsyncMock()

        await cm.connect("job-123", mock_ws)

        assert "job-123" in cm.active_connections
        assert mock_ws in cm.active_connections["job-123"]
        mock_ws.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connection_manager_connect_multiple(self):
        """Test multiple connections for same job."""
        cm = ConnectionManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()

        await cm.connect("job-123", mock_ws1)
        await cm.connect("job-123", mock_ws2)

        assert len(cm.active_connections["job-123"]) == 2

    @pytest.mark.asyncio
    async def test_connection_manager_disconnect(self):
        """Test disconnect removes websocket."""
        cm = ConnectionManager()
        mock_ws = AsyncMock()
        await cm.connect("job-123", mock_ws)

        cm.disconnect("job-123", mock_ws)

        assert "job-123" not in cm.active_connections

    @pytest.mark.asyncio
    async def test_connection_manager_disconnect_removes_empty_job(self):
        """Test disconnect removes job entry when no connections left."""
        cm = ConnectionManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        await cm.connect("job-123", mock_ws1)
        await cm.connect("job-123", mock_ws2)

        cm.disconnect("job-123", mock_ws1)
        assert "job-123" in cm.active_connections
        assert len(cm.active_connections["job-123"]) == 1

        cm.disconnect("job-123", mock_ws2)
        assert "job-123" not in cm.active_connections

    @pytest.mark.asyncio
    async def test_connection_manager_broadcast(self):
        """Test broadcast sends message to all connections."""
        cm = ConnectionManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        await cm.connect("job-123", mock_ws1)
        await cm.connect("job-123", mock_ws2)

        msg = ProgressMessage(
            job_id="job-123",
            task_type=ProductType.lesson,
            status=TaskStatus.in_progress,
            progress=50,
            message="Processing",
        )

        await cm.broadcast("job-123", msg)

        mock_ws1.send_text.assert_called_once()
        mock_ws2.send_text.assert_called_once()

        # Verify JSON format
        sent_json = mock_ws1.send_text.call_args[0][0]
        data = json.loads(sent_json)
        assert data["job_id"] == "job-123"
        assert data["progress"] == 50

    @pytest.mark.asyncio
    async def test_connection_manager_broadcast_no_connections(self):
        """Test broadcast handles job with no connections."""
        cm = ConnectionManager()

        msg = ProgressMessage(
            job_id="no-connections",
            task_type=ProductType.lesson,
            status=TaskStatus.completed,
            progress=100,
        )

        # Should not raise error
        await cm.broadcast("no-connections", msg)

    @pytest.mark.asyncio
    async def test_connection_manager_broadcast_cleans_dead_connections(self):
        """Test broadcast removes connections that fail to send."""
        cm = ConnectionManager()
        mock_ws_good = AsyncMock()
        mock_ws_bad = AsyncMock()
        mock_ws_bad.send_text.side_effect = Exception("Connection lost")

        await cm.connect("job-123", mock_ws_good)
        await cm.connect("job-123", mock_ws_bad)

        msg = ProgressMessage(
            job_id="job-123",
            task_type=ProductType.lesson,
            status=TaskStatus.in_progress,
            progress=10,
        )

        await cm.broadcast("job-123", msg)

        # Bad connection should be removed
        assert len(cm.active_connections["job-123"]) == 1
        assert mock_ws_good in cm.active_connections["job-123"]


class TestPushProgress:
    """Tests for push_progress function."""

    @pytest.mark.asyncio
    async def test_push_progress_creates_message(self):
        """Test push_progress creates correct ProgressMessage."""
        # Create a fresh manager for testing
        test_manager = ConnectionManager()
        mock_ws = AsyncMock()
        await test_manager.connect("test-job", mock_ws)

        # Patch the global manager temporarily
        from app.websocket import manager as original_manager
        import app.websocket
        app.websocket.manager = test_manager

        await push_progress(
            job_id="test-job",
            task_type=ProductType.ppt,
            status=TaskStatus.completed,
            progress=100,
            message="Done",
            download_url="/api/download/ppt/test-job",
        )

        mock_ws.send_text.assert_called_once()

        # Restore original manager
        app.websocket.manager = original_manager

    @pytest.mark.asyncio
    async def test_push_progress_with_error(self):
        """Test push_progress handles error parameter."""
        test_manager = ConnectionManager()
        mock_ws = AsyncMock()
        await test_manager.connect("error-job", mock_ws)

        from app.websocket import manager as original_manager
        import app.websocket
        app.websocket.manager = test_manager

        await push_progress(
            job_id="error-job",
            task_type=ProductType.lesson,
            status=TaskStatus.failed,
            progress=0,
            error="API timeout",
        )

        sent_json = mock_ws.send_text.call_args[0][0]
        data = json.loads(sent_json)
        assert data["error"] == "API timeout"

        app.websocket.manager = original_manager


class TestGlobalManager:
    """Tests for global ConnectionManager instance."""

    def test_global_manager_exists(self):
        """Test global manager is initialized."""
        from app.websocket import manager
        assert manager is not None
        assert isinstance(manager, ConnectionManager)

    def test_global_manager_is_singleton(self):
        """Test global manager is same instance."""
        from app.websocket import manager as m1
        from app.websocket import manager as m2
        assert m1 is m2