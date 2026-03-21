[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangnam-gu"]->.inner;
(
  nwr["leisure"="ice_rink"](area.inner)(area.outer);
);
out geom;
