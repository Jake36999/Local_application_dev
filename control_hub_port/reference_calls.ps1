# Reference LM Studio calls (run these directly against LM Studio, not the proxy)

# List models
Invoke-RestMethod -Method Get -Uri "http://localhost:1234/v1/models"

# Load a model (edit model id as needed)
Invoke-RestMethod -Method Post -Uri "http://localhost:1234/v1/models/astral-4b-coder/load" `
  -ContentType "application/json" `
  -Body '{"model":"astral-4b-coder","context_length":8192,"gpu_offload_ratio":0.5,"ttl":3600,"identifier":"session-1"}'

# Unload a model
Invoke-RestMethod -Method Post -Uri "http://localhost:1234/v1/models/astral-4b-coder/unload" `
  -ContentType "application/json" `
  -Body '{"model":"astral-4b-coder"}'

# Advanced /v1/responses example with tools
$body = @{
  model = "astral-4b-coder"
  input = "What is the weather like in Boston today?"
  tools = @(
    @{
      type = "function"
      name = "get_current_weather"
      description = "Get the current weather in a given location"
      parameters = @{
        type = "object"
        properties = @{
          location = @{
            type = "string"
            description = "The city and state, e.g. San Francisco, CA"
          }
          unit = @{
            type = "string"
            enum = @("celsius","fahrenheit")
          }
        }
        required = @("location","unit")
      }
    }
  )
  tool_choice = "auto"
} | ConvertTo-Json -Depth 8

Invoke-RestMethod -Method Post -Uri "http://localhost:1234/v1/responses" -ContentType "application/json" -Body $body
