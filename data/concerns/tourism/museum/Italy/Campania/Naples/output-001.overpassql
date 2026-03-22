[out:json][timeout:30];
area["name:en"="Campania"]->.outer;
area["name:en"="Naples"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;