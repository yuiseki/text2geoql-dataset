[out:json][timeout:30];
area["name:en"="Minami Ward"][boundary=administrative]->.outer;
area["name:en"="Kyoto"]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
