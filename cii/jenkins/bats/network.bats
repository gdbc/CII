#!/usr/bin/env bats
#A basic network test


@test "Check that I can ping my gateway" {
  gw=$(ip route show | grep default | cut -d" " -f3)
  run ping -c 1 ${gw}
}

@test "Check that I can resolve www.redhat.com" {
  run nslookup www.redhat.com 
}
