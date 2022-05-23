from coinex.coinex import CoinEx
# from somewhere_else import access_id, secret

coinex = CoinEx('208C0621123240C48DBA805C7C172412', '83FC10D422EF11CB57C5EAFF9F2F2B145DB79144281B8502')

# public API
# coinex.market_list()
# a=coinex.market_ticker('BCHBTC')
b=coinex.market_ticker_all()
# coinex.market_depth('BCHBTC')
# coinex.market_deals('BCHBTC')

# private API
# coinex.balance_info()
# coinex.balance_coin_withdraw_list()
# coinex.balance_coin_withdraw('BCH', 'qzjtuuc9nafvfhmwt47z84awltp9gmx7wyma3kvy9v', 0.001)
# coinex.balance_coin_withdraw_list(coin_withdraw_id=2465345342)
# coinex.balance_coin_withdraw_cancel(coin_withdraw_id=2465345342)
# coinex.order_limit('CETBCH', 'sell', 100.0, 10.0)
# coinex.order_market('CETBCH', 'buy', 1.0)
# coinex.order_ioc('CETBCH', 'sell', 100.0, 10.0)
# coinex.order_pending('CETBCH')
# coinex.order_finished('CETBCH')
# coinex.order_status('CETBCH', 2465345342)
# coinex.order_deals(2465345342)
# coinex.order_user_deals('CETBCH')
# coinex.order_pending_cancel('CETBCH', 2465345342)
# coinex.order_mining_difficulty()