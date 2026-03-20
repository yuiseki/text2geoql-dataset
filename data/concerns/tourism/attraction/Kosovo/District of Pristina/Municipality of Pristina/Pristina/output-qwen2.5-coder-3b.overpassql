[out:json][timeout:30];
area["name:en"="Pristina"][boundary=administrative]->.outer;
area["name:en"="Pristina"]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
