import tkinter as tk
from tkinter import ttk
import json
from binance_api import BinanceAPI
import threading
import time

class AccountManager:
    def __init__(self, root):
        self.root = root
        self.root.title("币安账户管理系统v0.0.1--蓝田")
        # 使用PhotoImage加载PNG图片
        icon = tk.PhotoImage(file="binance.png")
        self.root.tk.call('wm', 'iconphoto', self.root._w, icon)
        self.root.geometry("800x600")
        
        # 设置字体
        self.default_font = ('Microsoft YaHei UI', 10)  # 使用微软雅黑字体
        
        # 设置ttk样式
        self.style = ttk.Style()
        self.style.configure('Treeview', font=self.default_font)
        self.style.configure('Treeview.Heading', font=self.default_font)
        self.style.configure('TLabelframe.Label', font=self.default_font)
        self.style.configure('TLabel', font=self.default_font)
        
        # 加载账户配置
        self.accounts = self.load_accounts()
        
        # 创建标签页
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 为每个账户创建标签页
        self.account_tabs = {}
        for account_name, account_info in self.accounts.items():
            self.create_account_tab(account_name, account_info)
        
        # 启动更新线程
        self.running = True
        self.update_thread = threading.Thread(target=self.update_data)
        self.update_thread.daemon = True
        self.update_thread.start()

    def load_accounts(self):
        """从配置文件加载账户信息"""
        try:
            # 使用 utf-8 编码打开文件
            with open('accounts.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 示例账户配置
            return {
                "账户1": {"api_key": "your_api_key1", "api_secret": "your_secret1"},
                "账户2": {"api_key": "your_api_key2", "api_secret": "your_secret2"},
                "账户3": {"api_key": "your_api_key3", "api_secret": "your_secret3"},
                "账户4": {"api_key": "your_api_key4", "api_secret": "your_secret4"},
                "账户5": {"api_key": "your_api_key5", "api_secret": "your_secret5"}
            }

    def create_account_tab(self, account_name, account_info):
        """创建账户标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=account_name)
 
        
        # 创建三个Frame用于显示不同信息
        spot_frame = ttk.LabelFrame(tab, text="现货账户余额")
        futures_frame = ttk.LabelFrame(tab, text="合约账户余额")
        position_frame = ttk.LabelFrame(tab, text="合约持仓信息")
        
        spot_frame.pack(fill='both', expand=True, padx=5, pady=5)
        futures_frame.pack(fill='both', expand=True, padx=5, pady=5)
        position_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建Treeview
        spot_tree = self.create_spot_tree(spot_frame)
        futures_tree = self.create_futures_tree(futures_frame)
        position_tree = self.create_position_tree(position_frame)
        
        # 存储账户信息
        self.account_tabs[account_name] = {
            'api': BinanceAPI(
                api_key=account_info['api_key'],
                api_secret=account_info['api_secret'],
                proxy="http://127.0.0.1:7890"  # 代理设置
            ),
            'spot_tree': spot_tree,
            'futures_tree': futures_tree,
            'position_tree': position_tree
        }

    def create_spot_tree(self, parent):
        tree = ttk.Treeview(parent, columns=('asset', 'free', 'locked'), show='headings', height=5)
        tree.heading('asset', text='资产')
        tree.heading('free', text='可用')
        tree.heading('locked', text='冻结')
        
        # 设置列宽和对齐方式
        tree.column('asset', width=100, anchor='center')
        tree.column('free', width=150, anchor='center')
        tree.column('locked', width=150, anchor='center')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置组件
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        return tree

    def create_futures_tree(self, parent):
        tree = ttk.Treeview(parent, columns=('asset', 'balance', 'available'), show='headings',height=7)
        tree.heading('asset', text='资产')
        tree.heading('balance', text='余额')
        tree.heading('available', text='可用')
        
        # 设置列宽和对齐方式
        tree.column('asset', width=100, anchor='center')
        tree.column('balance', width=150, anchor='center')
        tree.column('available', width=150, anchor='center')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置组件
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        return tree

    def create_position_tree(self, parent):
        tree = ttk.Treeview(
            parent,
            columns=('symbol', 'position', 'entry_price', 'mark_price', 'pnl'),
            show='headings'
        )
        tree.heading('symbol', text='交易对')
        tree.heading('position', text='持仓量')
        tree.heading('entry_price', text='开仓价')
        tree.heading('mark_price', text='标记价')
        tree.heading('pnl', text='未实现盈亏')
        
        # 设置列宽和对齐方式
        tree.column('symbol', width=100, anchor='center')
        tree.column('position', width=100, anchor='center')
        tree.column('entry_price', width=100, anchor='center')
        tree.column('mark_price', width=100, anchor='center')
        tree.column('pnl', width=100, anchor='center')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置组件
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        return tree

    def update_account_data(self, account_name, account_data):
        """更新账户数据显示"""
        api = account_data['api']
        
        # 更新现货余额
        spot_balance = api.get_spot_balance()
        if spot_balance:
            tree = account_data['spot_tree']
            for item in tree.get_children():
                tree.delete(item)
            for asset in spot_balance:
                tree.insert('', 'end', values=(
                    asset['asset'],
                    asset['free'],
                    asset['locked']
                ))
        
        # 更新合约余额
        futures_balance = api.get_futures_balance()
        if futures_balance:
            tree = account_data['futures_tree']
            for item in tree.get_children():
                tree.delete(item)
            for asset in futures_balance:
                tree.insert('', 'end', values=(
                    asset['asset'],
                    asset['balance'],
                    asset['availableBalance']
                ))
        
        # 更新持仓信息
        positions = api.get_futures_positions()
        if positions:
            tree = account_data['position_tree']
            for item in tree.get_children():
                tree.delete(item)
            for pos in positions:
                tree.insert('', 'end', values=(
                    pos['symbol'],
                    pos['positionAmt'],
                    pos['entryPrice'],
                    pos['markPrice'],
                    f"{float(pos['unRealizedProfit']):.2f}"
                ))

    def update_data(self):
        """更新所有账户数据"""
        while self.running:
            try:
                for account_name, account_data in self.account_tabs.items():
                    self.update_account_data(account_name, account_data)
                time.sleep(5)  # 每5秒更新一次
            except Exception as e:
                print(f"更新数据时发生错误: {str(e)}")
                time.sleep(5)

    def on_closing(self):
        """关闭窗口时的处理"""
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop() 