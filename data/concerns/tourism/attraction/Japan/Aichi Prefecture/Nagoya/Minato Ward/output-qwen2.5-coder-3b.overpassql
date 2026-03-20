[out:json][timeout:30];
area["name:en"="Minato Ward"][boundary=administrative]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
