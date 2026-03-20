[out:json][timeout:30];
area["name:en"="Osaka"][boundary=administrative]->.outer;
area["name:en"="Osaka Prefecture"]->.inner;
(
  nwr["tourism"="guest_house"](area.inner)(area.outer);
);
out geom;
