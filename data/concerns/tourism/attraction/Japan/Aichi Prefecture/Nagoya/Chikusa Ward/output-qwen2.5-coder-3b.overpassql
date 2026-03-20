[out:json][timeout:30];
area["name:en"="Nagoya"][boundary=administrative]->.outer;
area["name:en"="Chikusa Ward"]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
