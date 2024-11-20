import asyncio

# Assuming the Router class we translated previously is in router.py
from fibrous_python import FibrousRouter

# Example of getting an object of supported protocols
async def main():
    # Create a new router instance
    router = FibrousRouter()

    try:
        protocols =  router.supported_protocols("scroll")
        print(protocols)
    except Exception as error:
        print(f"Error: {error}")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
