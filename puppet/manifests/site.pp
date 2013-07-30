node /tinge.*/ inherits default {
  class { margarine::tinge: }
}

node /blend.*/ inherits default {
  class { margarine::blend: }
}

node /spread.*/ inherits default {
  class { margarine::spread: }
}

node default {
  case $operatingsystem {
    "Ubuntu": {
      exec { "apt-get update":
        path => [ "/bin", "/usr/bin" ],
      }

      Exec["apt-get update"] -> Package <| |>
    }
  }
}

