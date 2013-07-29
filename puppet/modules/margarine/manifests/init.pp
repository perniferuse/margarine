# TODO Change the install directory after proper installation of margarine.
class margarine($directory = "/srv/www/margarine") {
  class { margarine::install: }
}
