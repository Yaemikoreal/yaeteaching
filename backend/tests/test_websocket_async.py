"""Tests for WebSocket connection management and async operations."""
import pytest
import pytest_asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.websocket import ConnectionManager, manager, push_progress
from models.job import ProgressMessage, TaskStatus, ProductType


class TestConnectionManagerAsync:
    """Tests for async WebSocket operations."""

    @pytest_asyncio.fixture
    async def async_manager(self):
        """Create fresh ConnectionManager for each test."""
        return ConnectionManager()

    @pytest.mark.asyncio
    async def test_connect_creates_connection_list(self, async_manager):
        """Test connect creates new connection list for job."""
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        await async_manager.connect("test-job", mock_ws)

        assert "test-job" in async_manager.active_connections
        assert mock_ws in async_manager.active_connections["test-job"]
        mock_ws.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_appends_to_existing_list(self, async_manager):
        """Test connect appends to existing connection list."""
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.accept = AsyncMock()

        await async_manager.connect("test-job", mock_ws1)
        await async_manager.connect("test-job", mock_ws2)

        assert len(async_manager.active_connections["test-job"]) == 2

    @pytest.mark.asyncio
    async def test_disconnect_removes_connection(self, async_manager):
        """Test disconnect removes connection from list."""
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()

        await async_manager.connect("test-job", mock_ws)
        async_manager.disconnect("test-job", mock_ws)

        assert "test-job" not in async_manager.active_connections

    @pytest.mark.asyncio
    async def test_disconnect_keeps_other_connections(self, async_manager):
        """Test disconnect only removes specified connection."""
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.accept = AsyncMock()

        await async_manager.connect("test-job", mock_ws1)
        await async_manager.connect("test-job", mock_ws2)

        async_manager.disconnect("test-job", mock_ws1)

        assert "test-job" in async_manager.active_connections
        assert mock_ws2 in async_manager.active_connections["test-job"]

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_all_connections(self, async_manager):
        """Test broadcast sends message to all connections."""
        mock_ws1 = AsyncMock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_text = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_text = AsyncMock()

        await async_manager.connect("test-job", mock_ws1)
        await async_manager.connect("test-job", mock_ws2)

        msg = ProgressMessage(
            job_id="test-job",
            task_type=ProductType.lesson,
            status=TaskStatus.in_progress,
            progress=50,
        )

        await async_manager.broadcast("test-job", msg)

        mock_ws1.send_text.assert_called_once()
        mock_ws2.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_skips_unknown_job(self, async_manager):
        """Test broadcast skips if job not found."""
        msg = ProgressMessage(
            job_id="unknown",
            task_type=ProductType.lesson,
            status=TaskStatus.pending,
            progress=0,
        )

        await async_manager.broadcast("unknown", msg)
        # Should not raise, just return

    @pytest.mark.asyncio
    async def test_broadcast_cleans_dead_connections(self, async_manager):
        """Test broadcast removes connections that fail to send."""
        mock_ws_good = AsyncMock()
        mock_ws_good.accept = AsyncMock()
        mock_ws_good.send_text = AsyncMock()
        mock_ws_bad = AsyncMock()
        mock_ws_bad.accept = AsyncMock()
        mock_ws_bad.send_text = AsyncMock(side_effect=Exception("Connection lost"))

        await async_manager.connect("test-job", mock_ws_good)
        await async_manager.connect("test-job", mock_ws_bad)

        msg = ProgressMessage(
            job_id="test-job",
            task_type=ProductType.lesson,
            status=TaskStatus.completed,
            progress=100,
        )

        await async_manager.broadcast("test-job", msg)

        # Bad connection should be removed
        assert mock_ws_bad not in async_manager.active_connections["test-job"]


class TestPushProgress:
    """Tests for push_progress function."""

    @pytest.mark.asyncio
    async def test_push_progress_broadcasts_message(self):
        """Test push_progress creates and broadcasts message."""
        test_manager = ConnectionManager()
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()

        await test_manager.connect("push-job", mock_ws)

        # Patch global manager
        with patch("app.websocket.manager", test_manager):
            await push_progress(
                job_id="push-job",
                task_type=ProductType.ppt,
                status=TaskStatus.in_progress,
                progress=75,
                message="Generating slides",
            )

        mock_ws.send_text.assert_called_once()
        call_data = json.loads(mock_ws.send_text.call_args[0][0])
        assert call_data["job_id"] == "push-job"
        assert call_data["progress"] == 75

    @pytest.mark.asyncio
    async def test_push_progress_with_download_url(self):
        """Test push_progress includes download URL when completed."""
        test_manager = ConnectionManager()
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()

        await test_manager.connect("download-job", mock_ws)

        with patch("app.websocket.manager", test_manager):
            await push_progress(
                job_id="download-job",
                task_type=ProductType.lesson,
                status=TaskStatus.completed,
                progress=100,
                download_url="/api/download/lesson/download-job",
            )

        call_data = json.loads(mock_ws.send_text.call_args[0][0])
        assert call_data["status"] == "completed"
        assert call_data["download_url"] == "/api/download/lesson/download-job"