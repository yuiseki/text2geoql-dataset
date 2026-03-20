[out:json][timeout:30];
area["name:en"="Yuen Long District"][boundary=administrative]->.outer;
area["name:en"="Hong Kong"][boundary=administrative]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
