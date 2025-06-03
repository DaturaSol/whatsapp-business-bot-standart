"""This is a shit stain in my code, rushed as fuck, will arise in erros """

from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Union, Dict, Any

from app.client_session.messages.models.base import WhatsAppRequestTo

class LanguageObject(BaseModel):
    code: str


class StaticHeaderComponent(BaseModel):
    type: Literal["header"] = Field(default="header")

class StaticBodyComponent(BaseModel):
    type: Literal["body"] = Field(default="body")


class FlowActionPayload(BaseModel):
    flow_token: str # Can be an empty string
    flow_action_data: Optional[Dict[str, Any]] = None

class ActionParameter(BaseModel):
    type: Literal["action"] = Field(default="action")
    action: FlowActionPayload

class FlowButtonComponent(BaseModel):
    type: Literal["button"] = Field(default="button")
    sub_type: Literal["flow"] = Field(default="flow")
    index: str # e.g., "0", "1", ...
    parameters: List[ActionParameter]

AnyTemplateComponent = Union[StaticHeaderComponent, StaticBodyComponent, FlowButtonComponent]

class TemplateObject(BaseModel):
    name: str
    language: LanguageObject
    components: List[AnyTemplateComponent]


class TemplateMessage(WhatsAppRequestTo):
    type_: Literal["template"] = Field(default="template", alias="type")
    template: TemplateObject

    def __init__(
        self,
        *,
        to: str,
        template_name: str,
        language_code: str = "pt_BR",
        has_static_header: bool, 
        has_flow_button: bool,
        # The index of the button (as a string, e.g., "0") that triggers the flow.
        flow_button_index: Optional[str] = None,
        # The flow_token. Can be an empty string if not otherwise needed.
        flow_token: str = "", # Defaults to empty string
        flow_action_data_payload: Optional[Dict[str, Any]] = None, 
        **kwargs,
    ):
        language_payload = LanguageObject(code=language_code)
        components_payload: List[AnyTemplateComponent] = []

        if has_static_header:
            components_payload.append(StaticHeaderComponent())

        # Body is always assumed to be present for any useful template
        components_payload.append(StaticBodyComponent())

        if has_flow_button:
            if flow_button_index is None:
                raise ValueError("flow_button_index is required if has_flow_button is True")

            action_payload_obj = FlowActionPayload(flow_token=flow_token, flow_action_data=flow_action_data_payload)
            # if flow_action_data_payload: # If you were to pass data
            #     action_payload_obj.flow_action_data = flow_action_data_payload

            action_parameter_obj = ActionParameter(action=action_payload_obj)
            
            flow_button_component = FlowButtonComponent(
                index=flow_button_index,
                parameters=[action_parameter_obj]
            )
            components_payload.append(flow_button_component)

        template_payload = TemplateObject(
            name=template_name,
            language=language_payload,
            components=components_payload
        )

        init_data = kwargs.copy()
        init_data["to"] = to
        init_data["template"] = template_payload
        
        super().__init__(**init_data)