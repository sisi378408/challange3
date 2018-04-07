mport os, sys, csv
from collections import namedtuple

IncomeTaxItem = namedtuple(
    'IncomeTaxItem',
    ['start', 'trate', 'sub']
)

INCOME_TAX_START_POINT = 3500

INCOME_TAX_QUICK_LOOKUP_TABLE = [
    IncomeTaxItem(80000, 0.45, 13505),
    IncomeTaxItem(55000, 0.35, 5505),
    IncomeTaxItem(35000, 0.30, 2755),
    IncomeTaxItem(9000, 0.25, 1005),
    IncomeTaxItem(4500, 0.2, 555),
    IncomeTaxItem(1500, 0.1, 105),
    IncomeTaxItem(0, 0.03, 0)
]

SOCIAL_INSURANCE_MONEY_RATE = {
    'endowment_insurance': 0.08,
    'medical_insurance': 0.02,
    'unemployment_insurance': 0.005,
    'employment_injury_insurance': 0,
    'maternity_insurance': 0,
    'public_accumulation_funds': 0.06
}

class Args:
    def __init__(self):
        l = sys.argv[1:]
        self.c = l[l.index('-c')+1]
        self.d = l[l.index('-d')+1]
        self.o = l[l.index('-o')+1]

args = Args()

class Userdata:
    def __init__(self):
        self.userdata = self._read_users_data()
    def _read_users_data(self):
        usrdata = []
        with open(args.d) as f:
            for line in f.readlines():
                employeeid,income = line.strip().split(',')
                print(employeeid,income)
                try:
                    income = int(income)
                except:
                    print('Parameter Error')
                    exit()
                usrdata.append((employeeid,income))
        return usrdata
    def __iter__(self):
        return iter(self.userdata)
userdata = Userdata().userdata
print('userdata:',userdata)

class Config:
    def __init__(self):
        d = {}
        with open(args.c) as f:
            for i in f:
                t = i.strip().split('=')
                d[t[0].strip()] = float(t[1].strip())
        self.data = d

    def _get_config(self, key):
        try:
            return self.data[key]
        except KeyError:
            print('Config Error')
            exit()

    @property
    def social_insurance_baseline_low(self):
        return self._get_config('JiShuL')

    @property
    def social_insurance_baseline_high(self):
        return self._get_config('JiShuH')

    @property
    def social_insurance_total_rate(self):
        return sum([
            self._get_config('YangLao'),
            self._get_config('YiLiao'),
            self._get_config('ShiYe'),
            self._get_config('GongShang'),
            self._get_config('ShengYu'),
            self._get_config('GongJiJin')
        ])

config = Config()


class Incometaxcalculator:
    def __init__(self,userdata):
        self.userdata = userdata
    @staticmethod
    def real_income(income):
        if income < config.social_insurance_baseline_low:
            social_insurance = config.social_insurance_baseline_low * config.social_insurance_total_rate
            real_income = income - social_insurance
            return social_insurance,real_income
        elif income > config.social_insurance_baseline_high:
            social_income = config.social_insurance_baseline_high * config.social_insurance_total_rate
            real_income = income -  social_income
            return social_insurance,real_income
        else:
            social_insurance = income * config.social_insurance_total_rate
            real_income = income - social_insurance
            return social_insurance,real_income
        
    @classmethod
    def calculator(cls,income):
        social_insurance,real_income = cls.real_income(income)
        tax_part = real_income - INCOME_TAX_START_POINT
        if tax_part < 0:
            return '0.00','{:.2f}'.format(real_income)
        for item in INCOME_TAX_QUICK_LOOKUP_TABLE:
            if tax_part > item.start:
                tax = tax_part*item.trate - item.sub
                salary = real_income - tax
                return '{:.2f}'.format(tax), '{:.2f}'.format(salary)
    def cal_user(self):
        usrincome = []
        for employee_id,income in self.userdata:
            temp = [employee_id,income]
            social_insurance,real_income = self.real_income(income)
            tax,salary = self.calculator(income)
            social_insurance = '{:.2f}'.format(social_insurance)
            temp += [social_insurance,tax,salary]
            usrincome.append(temp)
        print('usrincome:',usrincome)
        return usrincome
    def export(self, file_type='csv'):
        usrincome = self.cal_user()
        with open(args.o, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(usrincome)
if __name__ == '__main__':
    calculator = Incometaxcalculator(Userdata())
    calculator.export()

