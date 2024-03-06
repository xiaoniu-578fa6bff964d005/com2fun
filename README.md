# com2fun - Transform document into function.

This liabrary leverages [OpenAI API](https://github.com/openai/openai-python) to predict the output of a function based on its documentation.

## Install

```
pip install --upgrade com2fun
```

## Usage

Basic usage:
```
import com2fun

@com2fun.com2fun
def top(category: str, n) -> list[str]:
    """top n items"""

In  [1]: top("fish", 5)
Out [1]: ['salmon', 'tuna', 'cod', 'mackerel', 'halibut']
In  [2]: type(top("fish", 5))
Out [2]: list
In  [3]: top("Pen Brand", 3)
Out [3]: ['Pilot', 'Uni-ball', 'Zebra']
```

Specifiy output format by document:
```
@com2fun.com2fun
def SWOT(action: str) -> dict:
    """
    SWOT analysis is a powerful tool used to assess an organization’s strengths, 
    weaknesses, opportunities, and threats. It helps organizations focus their 
    resources and actions on areas where they have the most potential for success 
    and makes strategic decisions more transparent.
    
    Generate a SWOT analysis to assist business owners, managers, and individuals 
    in making tough decisions.
    
    Return a dictionary like 
    {
        "strengths": [ (summary, explanation), ...],
        "weaknesses": [...],
        "oppotunities": [...],
        "threats": [...],
    }
    """

In  [4]: print(SWOT("provide additional training for customer service staff"))
Out [4]:
{'strengths': [('Increased customer satisfaction',
   'Providing additional training for customer service staff will help them better understand customer needs and provide better service, leading to increased customer satisfaction.')],
 'weaknesses': [('Cost of training',
   'Providing additional training for customer service staff will require additional resources, such as time and money, which can be a significant cost to the organization.')],
 'opportunities': [('Improved customer service',
   'Providing additional training for customer service staff will help them better understand customer needs and provide better service, leading to improved customer service.')],
 'threats': [('Lack of resources',
   'Providing additional training for customer service staff may require additional resources, such as time and money, which may not be available to the organization.')]}
```

Chain of thought:
```
@com2fun.com2fun
def solve_elementary_math(question: str) -> dict:
    """
    {"debug": {"step by step explanation": list[str]},
     "return": float}
    """
In  [5]: solve_elementary_math("Maurita and Felice each take 4 tests. Here are the results of Maurita’s 4 tests: 4, 4, 4, 4. Here are the results for 3 of Felice’s 4 tests: 3, 3, 3. If Maurita’s mean for the 4 tests is 1 point higher than Felice’s, what’s the score of Felice’s 4th test?")
Out [5]:
{'debug': {'step by step explanation': ['Maurita and Felice each took 4 tests.',
   'Maurita got 4, 4, 4, 4 on her tests.',
   'Felice got 3, 3, 3 on 3 of her tests.',
   'Maurita’s mean for the 4 tests is 1 point higher than Felice’s.',
   'We need to find the score of Felice’s 4th test.',
   'Maurita’s mean is 4, so Felice’s mean must be 3.',
   'The sum of Felice’s 4 tests must be 3 + 3 + 3 + x = 12.',
   'Therefore, x = 12 - 9 = 3.',
   'The score of Felice’s 4th test is 3.']},
 'return': 3.0}
```

## Add Example

```
In  [1]: top.add_example('continents', 3)(['Asia', 'Africa', 'North America'])
```

## Set Client

By default, com2fun uses the OpenAI library `openai` globally. You can set the client for com2fun by 
```
@com2fun.com2fun(client=openai.OpenAI(api_key="your_api_key"))
```

Anthropic is also supported:
```
@com2fun.com2fun(
    SF=com2fun.SF.anthropic.AnthropicChatSF, client=anthropic.Anthropic()
)
```
