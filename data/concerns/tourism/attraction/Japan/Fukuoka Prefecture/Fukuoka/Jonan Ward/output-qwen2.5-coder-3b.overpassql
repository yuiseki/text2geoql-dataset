[out:json][timeout:30];
area["name:en"="Fukuoka"][boundary=administrative]->.outer;
area["name:en"="Fukuoka Prefecture"]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
