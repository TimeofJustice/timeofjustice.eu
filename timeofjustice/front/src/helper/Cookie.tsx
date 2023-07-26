import Cookies from 'universal-cookie';

const cookies = new Cookies();

export function trySetCookie(cname: string, cvalue: string, exdays = 30, isConsent = false) {
    if (!cookies.get('cookie_consent') && !isConsent) return;

    const expires = new Date();
    expires.setTime(expires.getTime() + (exdays * 24 * 60 * 60 * 1000));

    cookies.set(cname, cvalue, { path: '/', expires: expires });
}

export function getCookie(cname: string): string {
    return cookies.get(cname) as string;
}