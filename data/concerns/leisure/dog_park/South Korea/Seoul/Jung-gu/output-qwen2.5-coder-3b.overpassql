[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Jung-gu"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
