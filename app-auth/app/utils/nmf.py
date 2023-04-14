import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from app.schemas.classifier import ClassifierConfig
import pickle


def get_top_common_word(top: int, nmf_model: NMF, tfidf: TfidfVectorizer):
    for index, topic in enumerate(nmf_model.components_):
        print(f"The top {top} words for topic # {index}")
        print([tfidf.get_feature_names_out()[i] for i in topic.argsort()[-top:]])
        print("\n")


def tfidf_transform(query: any):
    # preprocess

    df = pd.DataFrame([r.__dict__ for r in query.all()])

    tfidf = TfidfVectorizer(max_df=0.95, min_df=1, stop_words="english")
    dtm = tfidf.fit_transform(df["cause"])

    return df, tfidf, dtm


def nmf_train(config: ClassifierConfig, query: any):
    # preprocess

    df, tfidf, dtm = tfidf_transform(query)

    # create instance of nmf
    nmf_model = NMF(n_components=config.topic, random_state=config.random_state)
    nmf_model.fit(dtm)

    # classifier
    topic_result = nmf_model.transform(dtm)
    # df["Topic"] = topic_result.argmax(axis=1)

    # save model
    pickle.dump(nmf_model, open("nmf_model.pkl", "wb"))

    # return df.to_dict(orient="records")


def nmf_get_topic(config: ClassifierConfig, query: any):
    # preprocess

    df, tfidf, dtm = tfidf_transform(query)

    # load model
    nmf_model = pickle.load(open("nmf_model.pkl", "rb"))
    nmf_model.fit(dtm)

    get_top_common_word(config.top_word, nmf_model, tfidf)

    # get topic
    topic_list = []
    for index, topic in enumerate(nmf_model.components_):
        topic_list.append(
            {
                "topic": index,
                "words": [
                    tfidf.get_feature_names_out()[i]
                    for i in topic.argsort()[-config.top_word :]
                ],
                "label": "",
            }
        )
    return topic_list


def nmf_predict(query: any, topic_dict: dict):
    # preprocess

    df, tfidf, dtm = tfidf_transform(query)
    # load model and predict
    nmf_model = pickle.load(open("nmf_model.pkl", "rb"))
    topic_result = nmf_model.transform(dtm)
    df["Topic"] = topic_result.argmax(axis=1)

    # add label
    df["Label"] = df["Topic"].map(topic_dict)

    return df


def predict_event(cause: str, topic_dict: dict):
    tfidf = TfidfVectorizer(stop_words="english")
    dtm = tfidf.fit_transform(cause.split())

    # load model and predict
    nmf_model = pickle.load(open("nmf_model.pkl", "rb"))
    topic_result = nmf_model.fit_transform(dtm)
    topic = topic_result.argmax(axis=1)[0]

    # add label
    label = topic_dict[topic]

    return label
