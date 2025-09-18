# Maintainer: vinegm <info AT vinegm D0T com>
pkgname='py-of-aces'
pkgver=1.0.0
pkgrel=1
pkgdesc="A blackjack TUI written in Python"
arch=('x86_64')
url="https://github.com/vinegm/Py-of-Aces"
license=('MIT')
depends=('python' 'python-blessed')
makedepends=('python-build' 'python-installer' 'git')
source=("https://github.com/vinegm/Py-of-Aces/archive/refs/tags/v${pkgver}.tar.gz")
sha256sums=('4a3044a6364e031cfd971712e20d78ff2a5a17fda68f44b5ffad5c11db7332b9')

build() {
    cd "$srcdir/Py-of-Aces-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/Py-of-Aces-${pkgver}"
    python -m installer --destdir="$pkgdir" dist/*.whl
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}

