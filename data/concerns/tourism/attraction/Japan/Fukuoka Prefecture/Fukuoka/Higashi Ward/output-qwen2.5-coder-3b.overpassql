[out:json][timeout:30];
area["name:ja"="福岡県"][boundary=administrative]->.outer;
area["name:ja"="福岡市"][boundary=administrative]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
