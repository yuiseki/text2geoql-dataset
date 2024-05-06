[out:json][timeout:30000];
area["name:en"="Seoul"]->.outer;
area["name:en"="Guro-gu"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
