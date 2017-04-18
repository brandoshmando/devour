from devour.consumers import DevourConsumer
from devour.django import common
from example.models import Solution, Problem
from .schemas import MathSchema
from ..config import BALANCED_CONSUMER_CONFIG

class BalancedMathConsumer(DevourConsumer):
    consumer_type = 'balanced_consumer'
    topic = 'math'
    config = BALANCED_CONSUMER_CONFIG
    schema_class = MathSchema

    def digest(self, offset, id, variables, solution_id, event):
        if event == common.UPDATE_EVENT and solution_id:
            sol = Solution.objects.get(id=solution_id)
        else:
            sol = Solution()

        if isinstance(variables, str) or isinstance(variables, unicode):
            formatted = [int(i.strip()) for i in variables.split(',')]
        elif isinstance(variables, list):
            formatted = [int(i) for i in variables]
        else:
            print "Ill formatted variables."
            return False

        sol.value = str(self.lcmm(*formatted))
        sol.save()

        # overcomplicating to demonstrate
        # override of auto_produce
        if event == common.CREATE_EVENT:
            prob = Problem.objects.only('solution').get(id=id)

            prob.solution = sol
            prob.save(produce=False)


        print "Solution for problem {0} {1}: {2}".format(id, event, sol.value)

    def gcd(self, a, b):
        """Return greatest common divisor using Euclid's Algorithm."""
        while b:
            a, b = b, a % b
        return a

    def lcm(self, a, b):
        """Return lowest common multiple."""
        return a * b // self.gcd(a, b)

    def lcmm(self, *args):
        """Return lcm of args."""
        return reduce(self.lcm, args)
