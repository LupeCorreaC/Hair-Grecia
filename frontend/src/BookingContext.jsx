import { createContext, useContext, useReducer } from 'react';

const BookingContext = createContext(null);
const initial = { service_id: '', barber_id: '', date: '', time: '' };
function bookingReducer(state, action) {
  switch (action.type) {
    case 'SET_SERVICE': return { ...state, service_id: action.value, time: '' };
    case 'SET_BARBER': return { ...state, barber_id: action.value, time: '' };
    case 'SET_DATE': return { ...state, date: action.value, time: '' };
    case 'SET_TIME': return { ...state, time: action.value };
    case 'RESET': return initial;
    default: return state;
  }
}
export function BookingProvider({ children }) {
  const [booking, dispatch] = useReducer(bookingReducer, initial);
  return <BookingContext.Provider value={{ booking, dispatch }}>{children}</BookingContext.Provider>;
}
export function useBooking() { return useContext(BookingContext); }
