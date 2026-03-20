[out:json][timeout:30];
area["name:en"="Nagoya"][boundary=administrative]->.outer;
area["name:en"="Aichi Prefecture"]->.inner;
(
  nwr["tourism"="motel"](area.inner)(area.outer);
);
out geom;
