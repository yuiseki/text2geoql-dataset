[out:json][timeout:30];
area["name:en"="Campania"]->.outer;
area["name:en"="Naples"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;