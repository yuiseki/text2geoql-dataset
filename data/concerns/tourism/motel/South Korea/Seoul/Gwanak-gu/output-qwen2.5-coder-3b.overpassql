[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gwanak-gu"]->.inner;
(
  nwr["tourism"="motel"](area.inner)(area.outer);
);
out geom;
