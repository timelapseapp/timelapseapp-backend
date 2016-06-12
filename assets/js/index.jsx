import React from 'react';
import Relay from 'react-relay';
import ReactDOM from 'react-dom';
import { browserHistory, applyRouterMiddleware, Router } from 'react-router';
import useRelay from 'react-router-relay';

import '../../node_modules/react-mdl/extra/material.js';
import Route from './routes/Route';

const rootNode = document.getElementById('react-app');
// const rootNode = document.createElement('div');
// document.body.appendChild(rootNode);


Relay.injectNetworkLayer(
  new Relay.DefaultNetworkLayer('http://timelapse-manager.aldryn.me/graphql', {
    credentials: 'same-origin',
  })
);


ReactDOM.render(
  <Router history={browserHistory} routes={Route} render={applyRouterMiddleware(useRelay)} environment={Relay.Store} />,
  rootNode
);
