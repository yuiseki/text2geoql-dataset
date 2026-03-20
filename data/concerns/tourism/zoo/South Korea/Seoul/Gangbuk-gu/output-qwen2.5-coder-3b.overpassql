[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangbuk-gu"]->.inner;
(
  nwr["tourism"="zoo"](area.inner)(area.outer);
);
out geom;
