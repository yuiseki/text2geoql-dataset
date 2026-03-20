[out:json][timeout:30];
area["name:en"="Iwatsuki Ward"][boundary=administrative]->.outer;
area["name:en"="Saitama"]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
