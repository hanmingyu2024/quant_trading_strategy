import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';
import store from '../store';

test('renders app header', () => {
    render(
        <Provider store={store}>
            <BrowserRouter>
                <App />
            </BrowserRouter>
        </Provider>
    );

    const headerElement = screen.getByRole('banner');
    expect(headerElement).toBeInTheDocument();
});
