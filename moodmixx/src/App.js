import React, { useState } from 'react'
import { Button } from "semantic-ui-react";
import './App.css'
import 'semantic-ui-css/semantic.min.css'
import Switch from 'react-ios-switch'
import { Routes, Route, Navigate } from "react-router-dom";
import Login from './Login';
import Advanced from './Advanced'
import { BrowserRouter } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="https://moodmixx-app-30a3f646f185.herokuapp.com/"
          element={
            <Navigate
              replace
              to="https://moodmixx-app-30a3f646f185.herokuapp.com/login"
            />
          }
        />
        <Route
          path="https://moodmixx-app-30a3f646f185.herokuapp.com/login"
          element={<Login />}
        />
        <Route
          path="https://moodmixx-app-30a3f646f185.herokuapp.com/content"
          element={<Advanced />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;