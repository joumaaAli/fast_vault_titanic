from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.common.models import DataRecord
import pandas as pd

df = pd.read_csv('./tested.csv')

df['Age'].fillna(df['Age'].mean(), inplace=True)
df['Cabin'].fillna('Unknown', inplace=True)
df['Embarked'].fillna('S', inplace=True)

df['Sex'] = df['Sex'].map({'male': 0, 'female': 1})
df['Embarked'] = df['Embarked'].map({'C': 0, 'Q': 1, 'S': 2})

Session = sessionmaker(bind=engine)
session = Session()

records = [DataRecord(
    id=row['PassengerId'],
    survived=row['Survived'],
    pclass=row['Pclass'],
    name=row['Name'],
    sex=row['Sex'],
    age=row['Age'],
    sibsp=row['SibSp'],
    parch=row['Parch'],
    ticket=row['Ticket'],
    fare=row['Fare'],
    cabin=row['Cabin'],
    embarked=row['Embarked']
) for _, row in df.iterrows()]

session.bulk_save_objects(records)
session.commit()

session.close()