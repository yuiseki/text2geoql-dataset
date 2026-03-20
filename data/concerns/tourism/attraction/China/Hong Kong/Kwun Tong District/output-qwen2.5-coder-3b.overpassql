[out:json][timeout:30];
area["name:en"="Kwun Tong District"][boundary=administrative]->.outer;
(
  nwr["tourism"="attraction"](area.outer);
);
out geom;
