import sys
import getopt
import time
from plotly.offline import init_notebook_mode, iplot
from utils.preprocess import crop_imgs, load_data, preprocess_data, preprocess_imgs, save_new_images, init_train_data, train_data_generator
from utils.trainer import setup_train, save_model, ModelTypes
from tensorflow.keras.callbacks import ModelCheckpoint
from utils.containts import *

# init_notebook_mode(connected=True)
argv = sys.argv[1:]
model_type: str = ""
try:
    opts, args = getopt.getopt(argv, "hm:", ["model="])
except getopt.GetoptError:
    print('main.py -m <model type>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('main.py -m <model type>')
        sys.exit()
    elif opt in ("-m", "--model"):
        model_type = arg


if __name__ == "__main__":
    model_type_dict: dict = {"VGG": ModelTypes.VGG,
                             "RESNET_50": ModelTypes.RESNET_50}

    init_train_data()
    X_val_prep, X_test_prep, y_val, y_test = preprocess_data()
    train_generator, validation_generator = train_data_generator()[:2]

    model_type: ModelTypes = model_type_dict[model_type.upper()]

    trainer = setup_train(_type=model_type)

    start = time.time()

    checkpoint_filepath: str = MODEL_DATA_PATH

    checkpoint_model_callback = ModelCheckpoint(
        filepath=checkpoint_filepath,
        save_weights_only=True,
        monitor='val_acc',
        mode='max',
        save_best_only=False)

    trainer_history = trainer.fit_generator(
        train_generator,
        epochs=100,
        validation_data=validation_generator,
        callbacks=[checkpoint_model_callback]
    )

    end = time.time()
    print(end - start)

    # validate on val set
    predictions = trainer.predict(X_test_prep)
    predictions = [1 if x > 0.5 else 0 for x in predictions]

    _, train_acc = trainer.evaluate(X_val_prep, y_val, verbose=0)
    _, test_acc = trainer.evaluate(X_test_prep, y_test, verbose=0)

    save_model(trainer, trainer_history,
               MODEL_DATA_PATH_SOLID, _type=model_type)
