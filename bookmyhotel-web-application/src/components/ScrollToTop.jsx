import { useEffect } from 'react'
import { useLocation, useNavigationType } from 'react-router-dom'

// this scrolls to the top whenever we navigate to a new page (like clicking a hotel card)
// but skips scrolling when the user is going back, so the browser can restore
// their previous scroll position naturally
function ScrollToTop() {
  const { pathname } = useLocation()
  const navigationType = useNavigationType()

  useEffect(() => {
    if (navigationType !== 'POP') {
      window.scrollTo(0, 0)
    }
  }, [pathname, navigationType])

  return null
}

export default ScrollToTop