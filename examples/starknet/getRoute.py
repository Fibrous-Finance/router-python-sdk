from fibrous_python import FibrousRouter  # Assuming the Router class we translated earlier is saved in router.py

async def main():
    chain_name = "starknet" 
    fibrous = FibrousRouter()  # Create a new Router instance

    # Get supported tokens
    tokens =  fibrous.supported_tokens(chain_name)
    try:
        token_in_address:str = tokens["usdt"]["address"] # Token in address it isn't right way to get token address. make sure to get the right token address
        token_out_address:str = tokens["usdc"]["address"] # Token out address it isn't right way to get token address. make sure to get the right token address
        token_in_decimals:int = tokens["usdc"]["decimals"]

        # Define input amount (1 usdt in token decimals)
        input_amount = 1 * 10 ** (int(token_in_decimals))  # Equivalent to BigNumber in Python

        # Reverse route option
        reverse = False

        # Get the best route
        route =  fibrous.get_best_route(
            input_amount,
            token_in_address,
            token_out_address,
            chain_name,
            options={"reverse": reverse}
        )
        print("Route:", route)

    except Exception as error:
        print(f"Error: {error}")

# Run the main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
