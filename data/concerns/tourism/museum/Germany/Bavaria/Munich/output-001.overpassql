[out:json][timeout:30];
area["name:en"="Bavaria"]->.outer;
area["name:en"="Munich"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;