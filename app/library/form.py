import inspect
from fastapi import Form
from pydantic import BaseModel
from pydantic.fields import ModelField
from typing import Type


# https://stackoverflow.com/questions/60127234/how-to-use-a-pydantic-model-with-form-data-in-fastapi
def as_form(cls: Type[BaseModel]):
  new_parameters = []

  for field_name, model_field in cls.__fields__.items():
    model_field: ModelField  # type: ignore

    new_parameters.append(
      inspect.Parameter(
        model_field.alias,
        inspect.Parameter.POSITIONAL_ONLY,
        default=Form(...) if model_field.required else Form(model_field.default),
        annotation=model_field.outer_type_,
      )
    )

  async def as_form_func(**data):
    return cls(**data)

  sig = inspect.signature(as_form_func)
  sig = sig.replace(parameters=new_parameters)
  as_form_func.__signature__ = sig  # type: ignore
  setattr(cls, 'as_form', as_form_func)
  return cls
