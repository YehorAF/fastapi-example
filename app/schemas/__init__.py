from typing import Annotated, Literal
from pydantic import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]
ReactionEnum = Literal["awful", "bad", "normal", "good", "awesome"]
RequestStatusEnum = Literal["waiting", "approved", "declined"]