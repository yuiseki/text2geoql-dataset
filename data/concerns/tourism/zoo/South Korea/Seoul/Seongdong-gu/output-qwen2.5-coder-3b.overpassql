[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Seongdong-gu"]->.inner;
(
  nwr["tourism"="zoo"](area.inner)(area.outer);
);
out geom;
