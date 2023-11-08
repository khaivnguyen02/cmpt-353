import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def main():
    labelled_data = pd.read_csv(sys.argv[1])
    unlabelled_data = pd.read_csv(sys.argv[2])

    X = labelled_data.loc[:, 'tmax-01':'snwd-12']
    y = labelled_data['city']
    X_unlabelled = unlabelled_data.loc[:, 'tmax-01':'snwd-12']

    X_train, X_test, y_train, y_test = train_test_split(X, y)

    model = make_pipeline(
        StandardScaler(),
        SVC(kernel='linear', C=0.1)
    )
    model.fit(X_train, y_train)
    print(model.score(X_test, y_test))

    predictions = model.predict(X_unlabelled)

    df = pd.DataFrame({'truth': y_test, 'prediction': model.predict(X_test)})
    # print(df[df['truth'] != df['prediction']])

    pd.Series(predictions).to_csv(sys.argv[3], index=False, header=False)


if __name__ == "__main__":
    main()
