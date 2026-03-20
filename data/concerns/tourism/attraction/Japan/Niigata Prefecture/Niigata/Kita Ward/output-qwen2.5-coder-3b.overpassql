[out:json][timeout:30];
area["name:en"="Niigata"][boundary=administrative]->.outer;
area["name:en"="Kita Ward"]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
