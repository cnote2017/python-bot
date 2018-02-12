import configargparse


def parse_arguments():
    print(':: Start of program ::')
    # Capture command line params
    parser = configargparse.ArgumentParser(
        description=__doc__,
        default_config_files=['/rules/default.ini'],
        formatter_class=configargparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-c', '--config',
        dest='config_file', is_config_file=True, default='rules/default.ini', type=str)
    parser.add_argument(
        '-s', '--symbol',
        help='Symbol eg. LTCBTC')
    parser.add_argument(
        '-e', '--exchange',
        help='Exchange name. eg. bitfinex, binance')
    parser.add_argument(
        '-t', '--timeframe',
        help='Time interval (eg. 15m, 3h, 1d) of candles. Default: 1h',
        default='1h')
    parser.add_argument(
        '-lt', '--limit',
        help='Number of candle bars requested. Default: 100',
        type=int,
        default=100)
    parser.add_argument(
        '-i', '--idle',
        help='Idle period in seconds. Default: 300',
        default='300')
    parser.add_argument(
        '-st', '--start_time',
        help='Start time filter (Unix timestamp). Default: 0',
        type=int)
    parser.add_argument(
        '-et', '--end_time',
        help='End time filter (Unix timestamp). Default: 0',
        type=int)
    parser.add_argument(
        '-rs1', '--rsi_range1',
        help='RSI range parameter (First). Default: 20,40',
        default='20,40')
    parser.add_argument(
        '-rs2', '--rsi_range2',
        help='RSI range parameter (Second). Default: 60,80',
        default='60,80')
    parser.add_argument(
        '--both_rsi',
        help='RSI switch, if 1 we are using both rs1, rs2, if 0 - only rsi1. Default: 1',
        default=1, type=int)
    parser.add_argument(
        '--MACD_trend_qty',
        help='MACD trend points qty. Default: 4',
        default=4, type=int)
    parser.add_argument(
        '--MACD_flat_qty',
        help='MACD flat part points qty. Default: 5',
        default=5, type=int)
    parser.add_argument(
        '--MACD_flat_range',
        help='MACD range for considering flat. Default: 0.10',
        default=0.10, type=float)
    parser.add_argument(
        '--RSI_trend_qty',
        help='RSI trend points qty. Default: 2',
        default=2, type=int)
    parser.add_argument(
        '--MACD_step',
        help='MACD expected change within trend on 1 step. Default: 0.05',
        default=0.05, type=float)
    parser.add_argument(
        '--MACD_change_direction',
        help='MACD 1 step change to be considered change of trend. Default: 0.3',
        default=0.3, type=float)
    parser.add_argument(
        '--MACD_strategy',
        help='MACD strategy : MACD crossing zero or MACD in uptrend. Default: MACD-zero',
        default='MACD-zero', type=str)
    parser.add_argument(
        '--stop_loss',
        help='Stop loss . Default: 0.02',
        default=0.02, type=float)
    parser.add_argument(
        '--take_profit',
        help='Take profit. Default: 0.05',
        default=0.05, type=float)
    parser.add_argument(
        '--max_orders',
        help='limit the number of orders the system can place (useful for system testing). Default: 20',
        default=20, type=int)

    args = parser.parse_args()

    if args.start_time:
        args.start_time = int(round(args.start_time * 1000))
    if args.end_time:
        args.end_time = int(round(args.end_time * 1000))

    args.rsi_range1 = args.rsi_range1.split(',')
    args.rsi_range2 = args.rsi_range2.split(',')

    print(args)
    return args