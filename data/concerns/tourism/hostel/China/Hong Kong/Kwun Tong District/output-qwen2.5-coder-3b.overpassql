[out:json][timeout:30];
area["name:en"="Hong Kong"][boundary=administrative]->.outer;
(
  nwr["tourism"="hostel"](area.outer);
);
out geom;
