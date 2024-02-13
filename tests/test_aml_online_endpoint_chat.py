# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from unittest.mock import Mock, patch

import os
import pytest

from pyrit.chat.aml_online_endpoint_chat import AMLOnlineEndpointChat
from pyrit.models import ChatMessage


@pytest.fixture
def aml_online_chat() -> AMLOnlineEndpointChat:
    aml_online_chat = AMLOnlineEndpointChat(
        endpoint_uri="http://aml-test-endpoint.com",
        api_key="valid_api_key",
    )
    return aml_online_chat


def test_initialization_with_required_parameters(
    aml_online_chat: AMLOnlineEndpointChat,
):
    assert aml_online_chat.endpoint_uri == "http://aml-test-endpoint.com"
    assert aml_online_chat.api_key == "valid_api_key"


def test_initialization_with_no_key_raises():
    os.environ[AMLOnlineEndpointChat.API_KEY_ENVIRONMENT_VARIABLE] = ""
    with pytest.raises(ValueError):
        AMLOnlineEndpointChat(endpoint_uri="http://aml-test-endpoint.com")


def test_initialization_with_no_api_raises():
    os.environ[AMLOnlineEndpointChat.ENDPOINT_URI_ENVIRONMENT_VARIABLE] = ""
    with pytest.raises(ValueError):
        AMLOnlineEndpointChat(api_key="xxxxx")


def test_get_headers_with_valid_api_key(aml_online_chat: AMLOnlineEndpointChat):
    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer valid_api_key",
    }
    assert aml_online_chat._get_headers() == expected_headers


def test_complete_chat(aml_online_chat: AMLOnlineEndpointChat):
    messages = [
        ChatMessage(role="user", content="user content"),
    ]

    with patch("pyrit.common.net_utility.make_request_and_raise_if_error") as mock:
        mock_response = Mock()
        mock_response.json.return_value = {"output": "extracted response"}
        mock.return_value = mock_response
        response = aml_online_chat.complete_chat(messages)
        assert response == "extracted response"
        mock.assert_called_once()


def test_complete_chat_bad_json_response(aml_online_chat: AMLOnlineEndpointChat):
    messages = [
        ChatMessage(role="user", content="user content"),
    ]

    with patch("pyrit.common.net_utility.make_request_and_raise_if_error") as mock:
        mock_response = Mock()
        mock_response.json.return_value = {"bad response"}
        mock.return_value = mock_response
        with pytest.raises(TypeError):
            aml_online_chat.complete_chat(messages)
