# Maintainer: vinegm <info AT vinegm D0T dev>
pkgname='py-of-aces'
pkgver=1.1.0
pkgrel=1
pkgdesc="A blackjack TUI written in Python"
arch=('any')
url="https://github.com/vinegm/Py-of-Aces"
license=('MIT')
depends=('python' 'python-blessed')
makedepends=('python-build' 'python-installer' 'python-poetry-core')
source=("https://github.com/vinegm/Py-of-Aces/archive/refs/tags/v${pkgver}.tar.gz")
sha256sums=('e0b8f395f40f9fb114b4717cc846bcbff47eadc085a88c131a674b512ad9a3d5')

build() {
    cd "$srcdir/Py-of-Aces-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/Py-of-Aces-${pkgver}"
    python -m installer --destdir="$pkgdir" dist/*.whl
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}

