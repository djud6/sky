import { createStore, applyMiddleware } from "redux";
import { persistReducer, persistStore } from "redux-persist";
import thunkMiddleware from "redux-thunk";
import storage from "redux-persist/lib/storage";
import logger from "redux-logger";
import reducer from "../root-reducer";

const initialState = {};

const persistConfig = {
  key: "root",
  storage: storage,
};

const persistedReducer = persistReducer(persistConfig, reducer);

const middlewares = [];
middlewares.push(thunkMiddleware);
if (process.env.NODE_ENV === "development") {
  middlewares.push(logger);
}

const store = createStore(persistedReducer, initialState, applyMiddleware(...middlewares));
const persistor = persistStore(store);

export { store, persistor };
