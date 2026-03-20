[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Saitama Prefecture"]->.inner;
(
  nwr["tourism"="guest_house"](area.inner)(area.outer);
);
out geom;
